from bs4 import BeautifulSoup
import requests
import re
from urllib.parse import urlparse, parse_qs

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from base64 import b64encode, b64decode

from json import loads

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0"
}


def keys_dict() -> dict:
    keys = {
        "kdrama": {
            "base_url": "https://draplay.info/",
            "encode_key": "93422192433952489752342908585752",
            "decrypt_key": "93422192433952489752342908585752",
            "iv": "9262859232435825",
        },
        "anime": {
            "base_url": "https://embtaku.pro/",
            "encode_key": "37911490979715163134003223491201",
            "decrypt_key": "54674138327930866480207815084989",
            "iv": "3134003223491201",
        },
    }

    return keys


class VideoSourceNotFound(Exception):
    def __init__(self, message="Video Source Not Found"):
        self.message = message
        super().__init__(self.message)


class VidstreamScraper:
    def __init__(self, mode: str = "kdrama"):
        self.mode = mode

        config = keys_dict()

        final_config = config.get(mode.lower())
        self.base_url, self.encode_key, self.decrypt_key, self.iv = (
            final_config.values()
        )

        self.encode_key = self.encode_key.encode() if self.encode_key else None
        self.decrypt_key = self.decrypt_key.encode() if self.decrypt_key else None
        self.iv = self.iv.encode() if self.iv else None

    def encrypt(self, message, key=None):
        iv = self.iv
        # Pad the message to be a multiple of 16 bytes
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(message) + padder.finalize()

        # Create an AES cipher object with the key, CBC mode, and the provided IV
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()

        # Encrypt the padded data
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()

        # Return the base64-encoded ciphertext
        return b64encode(ciphertext).decode("utf-8")

    def decrypt(self, ciphertext, key=None):
        iv = self.iv

        # Decode the base64-encoded ciphertext
        ciphertext = b64decode(ciphertext)

        # Create an AES cipher object with the key, CBC mode, and the provided IV
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()

        # Decrypt the ciphertext
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()

        # Unpad the decrypted data
        unpadder = padding.PKCS7(128).unpadder()
        message = unpadder.update(padded_data) + unpadder.finalize()

        # Return the decrypted message
        return message.decode("utf-8")

    def recently_added(self, page_number: int = 1):
        """
        Returns a list of recently added shows.
        @page_number: input of page number, by default set to 1
        """

        result = []
        next_page_number = page_number + 1
        page = requests.get(
            f"{self.base_url}/?page={page_number}", headers=HEADERS, verify=False
        )
        soup = BeautifulSoup(page.content, "html.parser")
        shows = soup.find("ul", class_="listing items")

        for show in shows.find_all("li"):
            result.append(
                {
                    "title": re.sub(
                        r"Episode.\d+",
                        "",
                        show.select_one("div[class='name']").get_text().strip(),
                    ),
                    "image": show.find("img").get("src"),
                    "href": f'{self.base_url}{show.find("a").get("href")}',
                    "date": show.find("span", class_="date").get_text(),
                }
            )
        return {"dramas": result, "next_page": next_page_number}

    def search(self, query: str) -> list:
        """
        Returns a list of shows matching the query.
        @query: Name of show to search.
        """

        result = []

        page = requests.get(
            f"{self.base_url}/search.html?keyword={query}",
            headers=HEADERS,
            verify=False,
        )
        soup = BeautifulSoup(page.content, "html.parser")
        shows = soup.find("ul", class_="listing items")

        for show in shows.find_all("li"):
            result.append(
                {
                    "title": re.sub(
                        r"Episode.\d+",
                        "",
                        show.select_one("div[class='name']").get_text().strip(),
                    ),
                    "image": show.find("img").get("src"),
                    "href": f'{self.base_url}{show.find("a").get("href")}',
                    "date": show.find("span", class_="date").get_text(),
                }
            )
        return result

    def episodes(self, url: str) -> list:
        """
        Returns a list of episodes for a show.
        @url: Video url
        """

        result = []

        page = requests.get(url, headers=HEADERS, verify=False)
        soup = BeautifulSoup(page.content, "html.parser")
        episodes = soup.find("ul", class_="listing items lists")

        for episode in episodes.find_all("li"):
            result.append(
                {
                    "title": episode.select_one("div[class='name']").get_text().strip(),
                    "image": episode.find("img").get("src"),
                    "href": f'{self.base_url}{episode.find("a").get("href")}',
                    "date": episode.find("span", class_="date").get_text(),
                }
            )
        return result

    def default_server(self, url: str) -> str:
        """
        Returns the direct video link.
        @url: Iframe url
        """
        page = requests.get(url, headers=HEADERS, verify=False)
        soup = BeautifulSoup(page.content, "html.parser")

        iframe_url = f"https:{soup.find('iframe').attrs.get('src')}"
        parsed_url = urlparse(iframe_url)

        parsed_parameters = parse_qs(parsed_url.query)
        parsed_parameters = {k: v[0] for k, v in parsed_parameters.items()}

        if parsed_parameters.get("id"):

            iframe_response = requests.get(iframe_url, headers=HEADERS, verify=False)
            iframe_soup = BeautifulSoup(iframe_response.content, "html.parser")
            encrypted_data = iframe_soup.find(
                "script",
                attrs={"data-name": "episode" if self.mode == "anime" else "crypto"},
            ).attrs.get("data-value")

            decrypted_data = self.decrypt(encrypted_data, key=self.encode_key)

            original_id = decrypted_data.split("&")[0]
            encrypted_id = self.encrypt(original_id.encode(), self.encode_key)

            ajax_encrypt_url = (
                self.base_url
                + "encrypt-ajax.php"
                + "?id="
                + encrypted_id
                + "&alias="
                + decrypted_data
            )

            rr = requests.get(
                url=ajax_encrypt_url,
                headers={**HEADERS, "X-Requested-With": "XMLHttpRequest"},
                verify=False,
            )
            if rr.status_code == 200:
                j_data = rr.json()
                encrupted_data = j_data["data"]
                decrypted_data = self.decrypt(encrupted_data, key=self.decrypt_key)

                parsed_json = loads(decrypted_data)
                return parsed_json
            else:
                raise VideoSourceNotFound()

        elif parsed_parameters.get("slug"):
            s_url = (
                f"{self.base_url}/streaming.php?slug={parsed_parameters.get('slug')}"
            )
            response = requests.get(s_url, verify=False)
            soup = BeautifulSoup(response.content, "html.parser")

            javascript_code = soup.select_one("script:nth-child(4)").text
            pattern = r'file:"(.*?)"'
            match = re.search(pattern, javascript_code, re.DOTALL)

            if match:
                file_link = match.group(1)
                result = {
                    "source": [
                        {"file": file_link},
                    ]
                }
                return result
            else:
                raise Exception("Unable to fetch Dircet Link!.")
