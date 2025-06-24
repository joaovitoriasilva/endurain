let externalConfig = null;

export async function getConfig() {
    if (externalConfig !== null) {
        return externalConfig;
    }
    return await fetch('/config.json')
      .then(response => response.json())
      .then(config => {
          externalConfig = config;
      });
}

await getConfig();
