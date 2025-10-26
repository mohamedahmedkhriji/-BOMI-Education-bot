# SSH Key Setup for GitHub Actions

## On Your VPS (as root):

```bash
# 1. Generate SSH key pair (press Enter for all prompts)
ssh-keygen -t rsa -b 4096 -f ~/.ssh/github_actions -N ""

# 2. Add public key to authorized_keys
cat ~/.ssh/github_actions.pub >> ~/.ssh/authorized_keys

# 3. Set correct permissions
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh

# 4. Display private key (copy this for GitHub secrets)
cat ~/.ssh/github_actions
```

## On GitHub:

1. Go to your repository: https://github.com/mohamedahmedkhriji/-BOMI-Education-bot
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add these secrets:

   - **VPS_HOST**: Your VPS IP address (e.g., 123.45.67.89)
   - **VPS_USERNAME**: root
   - **VPS_SSH_KEY**: Paste the entire private key from `cat ~/.ssh/github_actions`
     (Include `-----BEGIN OPENSSH PRIVATE KEY-----` and `-----END OPENSSH PRIVATE KEY-----`)

## Test SSH Connection:

```bash
# From your local machine
ssh -i ~/.ssh/github_actions root@YOUR_VPS_IP
```

Done! Push to main branch to trigger deployment.
