# Automated Workload Security AWS Connector

Automates the deployment of Workload Security's AWS Connectors.  

## What does it do?

This tool uses the `OrganizationAccountAccessRole` role to access your accounts. It then creates a `Workload_Security_Role_Cross` role and `Workload_Security_Policy_Cross` policy. These enable Workload Security's AWS Connector to work.

The tool then connects Workload Security to your AWS accounts. 


## Usage

1. Install dependencies:
   
   ```
   pip install --user -r requirements.txt
   ```

2. Create a CSV in the `src` directory. 
3. Enter `DisplayName` and `AccountNumber` details into the CSV file, like so:

    ```
    DisplayName,AccountNumber
    Account1,111111111111
    Account2,222222222222
    ```
    The `AccountNumber` column specifies the AWS account numbers. The `DisplayName` column defines what the accounts will be called in Workload Security.

4. Set the following environment variables:
   * `WS_KEY`: Deep Security API key
   *  `DS_URL`: Address of the Deep Security server **(only required for on-prem installs - Not required for Workload Security)**

5. Execute the following command in your AWS master accont:

   ```
   python run.py 
   ```

## Example

```
python run.py

Generating cross-account policy...
Setting up account 111111111111
Asssuming role: OrganizationAccountAccessRole
Got credentials from assumed role
Creating Trend cross-account role "Workload_Security_Role_Cross" using retrieved credentials...
Done
Creating cross-account policy "Workload_Security_Policy_Cross"
Done
Attaching cross-account policy "Workload_Security_Policy_Cross" to role
Done
Cross-account role was successfully created
Setting up account 222222222222
Asssuming role: OrganizationAccountAccessRole
Extracted credentials from assumed role
Creating Trend cross-account role "Workload_Security_Role_Cross" using extracted credentials...
Done
Creating cross-account policy "Workload_Security_Policy_Cross"
Done
Attaching cross-account policy "Workload_Security_Policy_Cross" to role
Done
Cross-account role was successfully created
Sleeping for 5 seconds to enable AWS policies to take effect...
Creating AWS Connector for "Account1" (111111111111). This may take a minute or two...
Done
Creating AWS Connector for "Account2" (222222222222). This may take a minute or two...
Done
```

## Customised names

The default role and policy names can be changed using the following command:

```
python run.py <custom_role_name> <custom_policy_name> 
```
