from config.config import default_config
from config.override_config import override_config


class ConfigProvider:

    def __init__(self, config=default_config, override_config=override_config):
        self.override_config = override_config.copy()
        self.config = config.copy()

    def get_config_for_video(self, video_name):
        # Provides the configuration for a given video. Attributes from self.override_config and self.config are merged
        # and in case the two configs share the same attribute, the override one has priority
        override_config_for_video = self.override_config.get(video_name, {})
        return self._merge_configs(self.config, override_config_for_video)

    def _merge_configs(self, config, override_config):
        merged_config = config.copy()
        for k, v in override_config.items():
            if k in config and isinstance(v, dict):
                merged_config[k] = self._merge_configs(config[k], v)
            else:
                merged_config[k] = v
        return merged_config
