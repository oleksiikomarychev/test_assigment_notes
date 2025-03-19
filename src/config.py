class Settings:
    database_url: str = "sqlite:///./test.db"
    test_database_url: str = "sqlite:///:memory:"


settings = Settings()
