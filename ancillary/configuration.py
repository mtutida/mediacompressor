
import json, os
from dataclasses import dataclass, asdict

CONFIG_FILE="config.json"

@dataclass(frozen=True)
class AppConfiguration:
    confirm_delete: bool = True
    auto_open_configuration_after_import: bool = False
    output_directory: str = ""
    output_filename_pattern: str = "{name}_compressed"
    use_source_directory: bool = True


class ConfigurationService:

    _instance=None

    def __init__(self):
        self._config=self._load()

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance=ConfigurationService()
        return cls._instance

    def get(self):
        return self._config

    def update(self, **kwargs):
        data=asdict(self._config)
        data.update(kwargs)
        new_cfg=AppConfiguration(**data)
        self._save(new_cfg)
        self._config=new_cfg

    def _load(self):
        if not os.path.exists(CONFIG_FILE):
            cfg=AppConfiguration()
            self._save(cfg)
            return cfg
        try:
            with open(CONFIG_FILE,"r",encoding="utf-8") as f:
                data=json.load(f)
            return AppConfiguration(**data)
        except Exception:
            cfg=AppConfiguration()
            self._save(cfg)
            return cfg

    def _save(self,cfg):
        tmp=CONFIG_FILE+".tmp"
        with open(tmp,"w",encoding="utf-8") as f:
            json.dump(asdict(cfg),f,indent=2)
        os.replace(tmp,CONFIG_FILE)
