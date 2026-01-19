# RestAPI MCP Server

## Overview
- This project will install `MCP - Model Context Protocol Server`, that provides configured REST API's as context to LLM's.
- Using this we can enable LLMs to do RestAPI's using prompts.
- Currently we support HTTP API Call's `GET/PUT/POST/PATCH/DELETE`.

## Installation
- Install package
  ```bash
  pip install restapi_mcp_server
  ```

## Claud Desktop
- Configuration details for Claud Desktop
  ```json
  {
    "mcpServers": {
      "restapi_mcp_server":{
        "command": "uv",
        "args": ["run","restapi_mcp_server"]
      }
    }
  }
  ```

### Configuration
- List of available environment variables
  - `DEBUG`: Enable debug logging (optional default is False)

## Contributing
Contributions are welcome.    
Please feel free to submit a Pull Request.

## License
This project is licensed under the terms of the MIT license.

## Github Stars
[![Star History Chart](https://api.star-history.com/svg?repos=rahgadda/restapi_mcp_server=Date)](https://star-history.com/#rahgadda/restapi_mcp_server&Date)

## Appendix
### UV
```bash
mkdir -m777 restapi_mcp_server
cd restapi_mcp_server
uv init
uv add mcp[cli] pydantic python-dotenv requests
uv add --dev twine setuptools
uv sync
uv run restapi_mcp_server
uv build
pip install --force-reinstall --no-deps .\dist\restapi_mcp_server-*fileversion*.whl
export TWINE_USERNAME="rahgadda"
export TWINE_USERNAME="<<API Key>>"
uv run twine upload --verbose dist/*
```

## Reference
- [UV Overview](https://www.youtube.com/watch?v=WKc2BdgmGZE)