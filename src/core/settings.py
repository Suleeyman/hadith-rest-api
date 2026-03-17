from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Hadislam Multilingual REST API"
    app_summary: str = "Multilingual REST API for most popular hadith editions : Sahih Al-Bukhari, Sahih Muslim, Jami At-Tirmidhi, Sunan Abu Dawud, Muwatta Malik, and much more. "
    app_description: str = """
# 📖 Hadislam REST API

The **Hadislam REST API** provides structured access to:

- The most popular hadith editions
- Each edition's book (i.e a *big* chapter)
- Each book's hadiths
- Multi-language support
- Optional pagination for collections

---

## 📜 License

This project is licensed under the MIT License.
    """
    app_version: str = "1.0.0"
    app_contact: dict[str, str] = {
        "name": "API Support",
        "url": "https://github.com/Suleeyman/hadislam.org",
        "email": "ozturksuleyman.dev@outlook.fr",
    }
    app_license: dict[str, str] = {
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
        "identifier": "MIT",
    }
    contact_email: str = "contact@hadislam.org"
    mongo_uri: str = ""
    mongo_db: str = ""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
