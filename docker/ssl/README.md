# SSL Certificates Directory

This directory should contain your SSL certificates for HTTPS.

## Required Files

1. `fullchain.pem` - The full certificate chain
2. `privkey.pem` - The private key

## Getting Certificates with Let's Encrypt

### Option 1: Standalone Mode (Recommended for first time)

```bash
# Install certbot
sudo apt-get update
sudo apt-get install certbot

# Get certificates (replace with your domain)
sudo certbot certonly --standalone -d wateen.health -d www.wateen.health

# Copy certificates to this directory
sudo cp /etc/letsencrypt/live/wateen.health/fullchain.pem ./fullchain.pem
sudo cp /etc/letsencrypt/live/wateen.health/privkey.pem ./privkey.pem

# Set permissions
sudo chown $USER:$USER *.pem
chmod 600 privkey.pem
chmod 644 fullchain.pem
```

### Option 2: DNS Challenge (For Cloudflare/other DNS)

```bash
# Install certbot with DNS plugin
sudo apt-get install python3-certbot-dns-cloudflare

# Create Cloudflare API token file
echo "dns_cloudflare_api_token = YOUR_CLOUDFLARE_API_TOKEN" > ~/.secrets/certbot/cloudflare.ini
chmod 600 ~/.secrets/certbot/cloudflare.ini

# Get certificates
sudo certbot certonly --dns-cloudflare --dns-cloudflare-credentials ~/.secrets/certbot/cloudflare.ini -d wateen.health -d www.wateen.health
```

### Option 3: Self-Signed (Development Only!)

```bash
# Generate self-signed certificate (NOT FOR PRODUCTION)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout privkey.pem \
  -out fullchain.pem \
  -subj "/CN=localhost"
```

## Certificate Renewal

Let's Encrypt certificates are valid for 90 days. Set up auto-renewal:

```bash
# Test renewal
sudo certbot renew --dry-run

# Add to crontab (runs twice daily)
sudo crontab -e

# Add this line:
0 0,12 * * * certbot renew --quiet --post-hook "docker restart wateen_nginx"
```

## File Permissions

```bash
# Private key should be readable only by owner
chmod 600 privkey.pem

# Certificate chain can be world-readable
chmod 644 fullchain.pem
```

## Security Notes

- NEVER commit private keys to version control
- The `.gitignore` should exclude `*.pem` files
- Rotate certificates annually at minimum
- Use strong key sizes (RSA 2048+ or ECDSA)
