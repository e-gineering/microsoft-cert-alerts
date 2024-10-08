<h2 align="center">microsoft-cert-alerts</h2>
<p align="center">Get notified when your certs are about to expire</p>

## About

This is a python script that runs on a schedule in Github Actions, and sends a reminder email as your certification gets close to expiring.

## Signing up for the emails

To add yourself to the list, add an entry to the `users` list in the [`certifications.yaml`](certifications.yaml) file.

The `email` can be any email address you want to receive alerts at, and you should be able to find the `credentialId` for each cert in your Microsoft Learn profile here:

https://learn.microsoft.com/en-us/users/me/credentials?tab=credentials-tab
