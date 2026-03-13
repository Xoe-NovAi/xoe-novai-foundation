const http = require('http');
const crypto = require('crypto');
const fs = require('fs');
const CLIENT_ID = process.env.GOOGLE_CLIENT_ID;
const CLIENT_SECRET = process.env.GOOGLE_CLIENT_SECRET;
const REDIRECT_URI = 'http://localhost:51121/oauth-callback';
const SCOPES = ['https://www.googleapis.com/auth/cloud-platform','https://www.googleapis.com/auth/userinfo.email','https://www.googleapis.com/auth/userinfo.profile','https://www.googleapis.com/auth/cclog','https://www.googleapis.com/auth/experimentsandconfigs','openid'];
function base64url(buf) { return buf.toString('base64').replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, ''); }
const verifier = base64url(crypto.randomBytes(32));
const challenge = base64url(crypto.createHash('sha256').update(verifier).digest());
const state = base64url(Buffer.from(JSON.stringify({ verifier, projectId: '' })));
const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${CLIENT_ID}\&redirect_uri=${encodeURIComponent(REDIRECT_URI)}\&response_type=code\&scope=${encodeURIComponent(SCOPES.join(' '))}\&state=${state}\&code_challenge=${challenge}\&code_challenge_method=S256\&access_type=offline\&prompt=consent`;
console.log('
=== Antigravity Direct Login ===
');
console.log('1. Open this URL in your browser:
');
console.log(authUrl);
console.log('
2. Sign in and Allow access.');
const server = http.createServer((req, res) => {
    const url = new URL(req.url, `http://${req.headers.host}`);
    if (url.pathname === '/oauth-callback') {
        const code = url.searchParams.get('code');
        if (code) {
            console.log('
Received code! Exchanging...');
            exchangeCode(code, verifier);
            res.end('Login successful! Return to terminal.');
        }
    }
    res.end('Waiting...');
});
server.listen(51121, () => { console.log('Waiting for callback on http://localhost:51121...'); });
async function exchangeCode(code, verifier) {
    try {
        const body = new URLSearchParams({ client_id: CLIENT_ID, client_secret: CLIENT_SECRET, code, grant_type: 'authorization_code', redirect_uri: REDIRECT_URI, code_verifier: verifier });
        const response = await fetch('https://oauth2.googleapis.com/token', { method: 'POST', body });
        const tokens = await response.json();
        const userRes = await fetch('https://www.googleapis.com/oauth2/v1/userinfo?alt=json', { headers: { Authorization: `Bearer ${tokens.access_token}` } });
        const user = await userRes.json();
        const accountsPath = `${require('os').homedir()}/.config/opencode/antigravity-accounts.json`;
        let accounts = { version: 4, accounts: [], activeIndex: 0, activeIndexByFamily: { claude: 0, gemini: 0 } };
        const newAccount = { email: user.email, refreshToken: tokens.refresh_token, projectId: 'rising-fact-p41fc', managedProjectId: 'rising-fact-p41fc', addedAt: Date.now(), lastUsed: Date.now(), enabled: true };
        accounts.accounts.push(newAccount);
        fs.writeFileSync(accountsPath, JSON.stringify(accounts, null, 2));
        const authPath = `${require('os').homedir()}/.local/share/opencode/auth.json`;
        let auth = fs.existsSync(authPath) ? JSON.parse(fs.readFileSync(authPath, 'utf8')) : {};
        auth.google = { type: 'oauth', access: tokens.access_token, refresh: `${tokens.refresh_token}|rising-fact-p41fc`, expires: Date.now() + (tokens.expires_in * 1000) };
        fs.writeFileSync(authPath, JSON.stringify(auth, null, 2));
        console.log(`
SUCCESS! ${user.email} added.`);
        process.exit(0);
    } catch (e) { console.error(e); process.exit(1); }
}
