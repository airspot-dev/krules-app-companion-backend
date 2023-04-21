from fastapi.middleware.cors import CORSMiddleware
middlewares = [
    (
        CORSMiddleware,
        {
            "allow_origins": [
                "http://localhost:4200",
                "https://krules-app-companion-hgt7kizkdq-oc.a.run.app/"
            ],
            "allow_credentials": True,
            "allow_methods": ["*"],
            "allow_headers": ["*"],
        }
    )
]
