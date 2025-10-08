# Traefik Reverse Proxy

We will choose [Traefik](https://doc.traefik.io/traefik/) as our reverse proxy, as it has both Docker and Kubernetes support and a large number of predefined [middleware](https://doc.traefik.io/traefik/reference/routing-configuration/http/middlewares/overview/) types, for example:

- Authentication: BasicAuth and ForwardAuth.
- RateLimit
- Routing: StripPrefix, RedirectRegex, RedirectScheme

## Password file for platform-wide authentication (BasicAuth)

Currently, BasicAuth is set up platform-wide via `infra/traefik/dynamic.yml`.  The password file for the BasicAuth middleware is stored at `infra/traefik/htpasswd` (mounted as `/etc/traefik/htpasswd` in the container).  Since we need at minimum an admin account, create this file using:

```sh
htpasswd -cB infra/traefik/htpasswd admin
```

To update the password file, use:

```sh
htpasswd -bB infra/traefik/htpasswd <user> <password>  # Update from command-line
htpasswd -iB infra/traefik/htpasswd <user> <password>  # Update from stdin
htpasswd -D infra/traefik/htpasswd <user>  # Delete user
```

!!!note
    The `-B` flag specifies bcrypt encryption.

!!!warning
    Each service in the DT platform should authorize each incoming request, as BasicAuth only performs authentication/authorization at the **platform** level.

## 🚧 Authentication and permissions lookup using ForwardAuth and PostgreSQL (TODO)

This section is forthcoming.

## 🚧 SSL/TLS setup with Let's Encrypt (TODO)

This section is forthcoming.
