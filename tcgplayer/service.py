import logging
import platform
from json import JSONDecodeError
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

from pydantic import ValidationError, parse_obj_as
from ratelimit import limits, sleep_and_retry
from requests import get, post
from requests.exceptions import ConnectionError, HTTPError, ReadTimeout

from tcgplayer import __version__
from tcgplayer.exceptions import ServiceError
from tcgplayer.schemas.category import Category
from tcgplayer.schemas.condition import Condition
from tcgplayer.schemas.group import Group
from tcgplayer.schemas.language import Language
from tcgplayer.schemas.price import Price
from tcgplayer.schemas.printing import Printing
from tcgplayer.schemas.product import Product
from tcgplayer.schemas.rarity import Rarity
from tcgplayer.sqlite_cache import SQLiteCache

LOGGER = logging.getLogger(__name__)
MINUTE = 60


class TCGPlayer:
    API_URL = "https://api.tcgplayer.com/v1.39.0"

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        access_token: Optional[str] = None,
        timeout: int = 30,
        cache: Optional[SQLiteCache] = None,
    ):
        self.headers = {
            "Accept": "application/json",
            "User-Agent": f"TCG-Player-Wrapper/{__version__}"
            f"/{platform.system()}: {platform.release()}",
        }
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        if self.access_token:
            self.headers["Authorization"] = f"Bearer {self.access_token}"

        self.timeout = timeout
        self.cache = cache

    @sleep_and_retry
    @limits(calls=20, period=MINUTE)
    def _perform_get_request(self, url: str, params: Dict[str, str] = None) -> Dict[str, Any]:
        if params is None:
            params = {}

        try:
            response = get(url, params=params, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except ConnectionError as ce:
            raise ServiceError(f"Unable to connect to `{url}`: {ce}")
        except HTTPError as he:
            raise ServiceError(he.response.text)
        except ReadTimeout:
            raise ServiceError("Server took too long to response")
        except JSONDecodeError as de:
            raise ServiceError(f"Invalid response from `{url}`: {de}")

    @sleep_and_retry
    @limits(calls=20, period=MINUTE)
    def _post_request(
        self, endpoint: str, params: Dict[str, str] = None, body: Dict[str, str] = None
    ) -> Dict[str, Any]:
        if params is None:
            params = {}
        if body is None:
            body = {}

        url = self.API_URL + endpoint

        try:
            response = post(
                url, params=params, data=body, headers=self.headers, timeout=self.timeout
            )
            response.raise_for_status()
            content = response.json()
            if "error_description" in content and content["error_description"]:
                raise ServiceError(content["error_description"])
            return content
        except ConnectionError as ce:
            raise ServiceError(f"Unable to connect to `{url}`: {ce}")
        except HTTPError as he:
            raise ServiceError(he.response.text)
        except ReadTimeout:
            raise ServiceError("Server took too long to response")
        except JSONDecodeError as de:
            raise ServiceError(f"Invalid response from `{url}`: {de}")

    def _get_request(
        self,
        endpoint: str,
        params: Dict[str, str] = None,
        skip_cache: bool = False,
    ) -> Dict[str, Any]:
        cache_params = f"?{urlencode(params)}" if params else ""

        url = self.API_URL + endpoint
        cache_key = f"{url}{cache_params}"

        if self.cache and not skip_cache:
            if cached_response := self.cache.select(cache_key):
                return cached_response

        response = self._perform_get_request(url=url, params=params)
        if not response:
            return {}
        if "error_description" in response and response["error_description"]:
            raise ServiceError(response["error_description"])

        if self.cache and not skip_cache:
            self.cache.insert(cache_key, response)

        return response

    def generate_token(self) -> str:
        LOGGER.info("Generating new Auth Token")
        if "Authorization" in self.headers:
            del self.headers["Authorization"]
        token = self._post_request(
            endpoint="/token",
            body={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
        )["access_token"]
        self.access_token = token
        self.headers["Authorization"] = f"Bearer {token}"
        return token

    def authorization_check(self) -> bool:
        try:
            self._get_request(endpoint="/catalog/categories", skip_cache=True)
            return True
        except ServiceError:
            self.access_token = None
            if "Authorization" in self.headers:
                del self.headers["Authorization"]
        return False

    def list_categories(self) -> List[Category]:
        try:
            results = self._retrieve_all_results(endpoint="/catalog/categories")
            # print(results)
            return parse_obj_as(List[Category], results)
        except ValidationError as err:
            raise ServiceError(err)

    def category(self, category_id: int) -> Category:
        try:
            result = self._get_request(endpoint=f"/catalog/categories/{category_id}")["results"][0]
            return Category(**result)
        except ValidationError as err:
            raise ServiceError(err)

    def list_category_groups(self, category_id: int) -> List[Group]:
        try:
            results = self._retrieve_all_results(
                endpoint=f"/catalog/categories/{category_id}/groups"
            )
            return parse_obj_as(List[Group], results)
        except ValidationError as err:
            raise ServiceError(err)

    def list_category_rarities(self, category_id: int) -> List[Rarity]:
        try:
            results = self._get_request(endpoint=f"/catalog/categories/{category_id}/rarities")[
                "results"
            ]
            return parse_obj_as(List[Rarity], results)
        except ValidationError as err:
            raise ServiceError(err)

    def list_category_printings(self, category_id: int) -> List[Printing]:
        try:
            results = self._get_request(endpoint=f"/catalog/categories/{category_id}/printings")[
                "results"
            ]
            return parse_obj_as(List[Printing], results)
        except ValidationError as err:
            raise ServiceError(err)

    def list_category_conditions(self, category_id: int) -> List[Condition]:
        try:
            results = self._get_request(endpoint=f"/catalog/categories/{category_id}/conditions")[
                "results"
            ]
            return parse_obj_as(List[Condition], results)
        except ValidationError as err:
            raise ServiceError(err)

    def list_category_languages(self, category_id: int) -> List[Language]:
        try:
            results = self._get_request(endpoint=f"/catalog/categories/{category_id}/languages")[
                "results"
            ]
            return parse_obj_as(List[Language], results)
        except ValidationError as err:
            raise ServiceError(err)

    def group(self, group_id: int) -> Group:
        try:
            result = self._get_request(endpoint=f"/catalog/groups/{group_id}")["results"][0]
            return Group(**result)
        except ValidationError as err:
            raise ServiceError(err)

    def list_group_products(self, category_id: int, group_id: int) -> List[Product]:
        try:
            results = self._retrieve_all_results(
                endpoint="/catalog/products",
                params={"categoryId": category_id, "groupId": group_id, "productTypes": "Cards"},
            )
            return parse_obj_as(List[Product], results)
        except ValidationError as err:
            raise ServiceError(err)

    def product(self, product_id: int) -> Product:
        try:
            result = self._get_request(endpoint=f"/catalog/products/{product_id}")["results"][0]
            return Product(**result)
        except ValidationError as err:
            raise ServiceError(err)

    def list_group_prices(self, group_id: int) -> List[Price]:
        try:
            results = self._get_request(endpoint=f"/pricing/group/{group_id}")["results"]
            return parse_obj_as(List[Price], results)
        except ValidationError as err:
            raise ServiceError(err)

    def product_prices(self, product_id: int) -> List[Price]:
        try:
            results = self._get_request(endpoint=f"/pricing/product/{product_id}")["results"]
            return parse_obj_as(List[Price], results)
        except ValidationError as err:
            raise ServiceError(err)

    def _retrieve_all_results(self, endpoint: str, params: Dict[str, str] = None) -> List[Any]:
        if params is None:
            params = {}
        params["limit"] = 100
        params["offset"] = 0

        response = self._get_request(endpoint, params=params)
        if not response:
            return []
        results = response["results"]
        while response["totalItems"] > len(results):
            params["offset"] = len(results)
            response = self._get_request(endpoint, params=params)
            results.extend(response["results"])
        return results
