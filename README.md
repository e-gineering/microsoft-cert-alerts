<h2 align="center">microsoft-cert-alerts</h2>
<h3 align="center">Get notified when your certs are about to expire</h2>

## About

This is a python script that runs on a schedule in Github Actions, and sends a reminder email as your certification gets close to expiring.

## Signing up for the emails

To add yourself to the list, add an entry to the `users` list in the [`certifications.yaml`](certifications.yaml) file. The `email` is the one you want to receive alerts at, and the `certificationId` you should be able to find on your Microsoft Learn profile.
