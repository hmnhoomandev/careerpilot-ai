# CareerPilot Google Cloud infrastructure

This root module describes isolated test, staging, and production stacks in
Zurich (`europe-west6`). It is deliberately not applied by CI. The placeholder
project IDs and image digests are plan-only examples, not real resources.

Authentication uses Application Default Credentials for an engineer and
Workload Identity Federation for CI. Service-account keys are prohibited.
Production changes require a reviewed plan, explicit owner approval, protected
environment approval, and a separately authorized apply.

```bash
terraform init -backend=false
terraform fmt -check -recursive
terraform validate
terraform plan -refresh=false -var-file=environments/test.tfvars -out=.artifacts/test.tfplan
```

No command above should be interpreted as approval to create a cloud resource.
Before first apply, replace placeholders, configure a remote state bucket with
versioning/CMEK, run a cost estimate, and complete the deployment checklist.
