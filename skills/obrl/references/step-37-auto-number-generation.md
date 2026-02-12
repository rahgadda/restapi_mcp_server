### Step 37 — AUTO_NUMBER_GENERATION (Create and Authorize Auto Number)
- Do not replace any json payload values.
- Purpose:
  - Create Auto Number Generation definition and then authorize it.
- Execution Condition:
  - Execute when `BRANCH-CODE`, `MAKER-ID`, and `CHECKER-ID` are available.
- Tool Used:
  ```
  mcp restapi-mcp-server -> createRestAPICall
  ```

- Create Auto Number
  ```json
  {
    "method":"POST",
    "action":"POPULATE-AUTONUMBER",
    "environment":"OBRL-14.8.2-RAH",
    "session":"{{SESSION_ID}}",
    "url":"{{OBRL-LN-MAINTENANCE-SERVICES}}/service/v14.8.1.0.0/identifierDefinitions",
    "request_headers":{
      "Content-Type":"application/json",
      "userId":"{{MAKER-ID}}",
      "branchCode":"{{BRANCH-CODE}}",
      "appId":"OBRLMANT",
      "entityId":"DEFAULTENTITY",
      "authToken":"y"
    },
    "request_body":{
      "productProcessor": "OBRL",
      "entityTypeCd": "ACC_NUM",
      "branch": "{{BRANCH-CODE}}",
      "maxLength": 17,
      "fixedLength": true,
      "checkSum": false,
      "userSeqResetFreqCd": "ANNUAL",
      "systemSeqName": "ACC_SEQ",
      "RlTmIdentifierParametersDTO": [
        {
          "sequenceNumber": 1,
          "unitsCd": "CONSTANT",
          "value": "VLN",
          "enable": true
        },
        {
          "sequenceNumber": 2,
          "unitsCd": "VARIABLE_CODE",
          "value": "PRDSEG_CD",
          "enable": true
        },
        {
          "sequenceNumber": 3,
          "unitsCd": "VARIABLE_CODE",
          "value": "BRN_CD",
          "enable": true
        },
        {
          "sequenceNumber": 4,
          "unitsCd": "SYS_SEQ",
          "value": 7,
          "enable": true
        }
      ]
    },
    "post_script": {
      "{{AUTONUMBER-KEYID}}": "jq_expression('.messages.keyId', $RESPONSE_BODY)"
    }
  }
  ```

 - Authorize (run only on success)
   - Execution Condition: Run this call only if the Create Auto Number call returned HTTP 2xx and `{{AUTONUMBER-KEYID}}` exists in the environment store.
  ```json
  {
    "method":"PATCH",
    "action":"AUTHORIZE-AUTONUMBER",
    "environment":"OBRL-14.8.2-RAH",
    "session":"<<session id created or available>>",
    "url":"{{OBRL-LN-MAINTENANCE-SERVICES}}/service/v14.8.1.0.0/identifierDefinitions/ACC_NUM:{{BRANCH-CODE}}:OBRL/approve",
    "request_headers":{
      "Content-Type":"application/json",
      "userId":"{{CHECKER-ID}}",
      "branchCode":"{{BRANCH-CODE}}",
      "appId":"OBRLMANT",
      "entityId":"DEFAULTENTITY",
      "authToken":"y"
    },
    "request_body":{
      "id":"{{AUTONUMBER-KEYID}}",
      "modNos":[1],
      "remarks":"approved"
    }
  }
  ```

- Success Conditions:
  - `AUTONUMBER-KEYID` is stored in the env store after Create call.
  - Authorize returns HTTP 2xx.
