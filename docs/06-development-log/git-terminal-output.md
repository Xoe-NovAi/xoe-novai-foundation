arcana-novai@Arcana-NovAi:~/Documents/xnai-foundation$ git push origin feature/multi-account-hardening
Enumerating objects: 610, done.
Counting objects: 100% (610/610), done.
Delta compression using up to 16 threads
Compressing objects: 100% (531/531), done.
Writing objects: 100% (546/546), 1.18 MiB | 357.00 KiB/s, done.
Total 546 (delta 151), reused 0 (delta 0), pack-reused 0 (from 0)
remote: Resolving deltas: 100% (151/151), completed with 37 local objects.
remote: error: GH013: Repository rule violations found for refs/heads/feature/multi-account-hardening.
remote: 
remote: - GITHUB PUSH PROTECTION
remote:   —————————————————————————————————————————
remote:     Resolve the following violations before pushing again
remote: 
remote:     - Push cannot contain secrets
remote: 
remote:     
remote:      (?) Learn how to resolve a blocked push
remote:      https://docs.github.com/code-security/secret-scanning/working-with-secret-scanning-and-push-protection/working-with-push-protection-from-the-command-line#resolving-a-blocked-push
remote:     
remote:      (?) This repository does not have Secret Scanning enabled, but is eligible. Enable Secret Scanning to view and manage detected secrets.
remote:      Visit the repository settings page, https://github.com/Xoe-NovAi/xoe-novai-foundation/settings/security_analysis
remote:     
remote:     
remote:       —— GitHub Personal Access Token ——————————————————————
remote:        locations:
remote:          - commit: f34b9ebabcb668184de2878c9f7fc0367dda732f
remote:            path: FIRST-OpenCode-MC-Overseer-strategy-and-dev-session-ses_37a1.md:7320
remote:          - commit: f34b9ebabcb668184de2878c9f7fc0367dda732f
remote:            path: FIRST-OpenCode-MC-Overseer-strategy-and-dev-session-ses_37a1.md:12533
remote:     
remote:        (?) To push, remove secret from commit(s) or follow this URL to allow the secret.
remote:        https://github.com/Xoe-NovAi/xoe-novai-foundation/security/secret-scanning/unblock-secret/3AE01dZvsrY8pLKIsOKfZnrkiX9
remote:     
remote: 
remote: 
To https://github.com/Xoe-NovAi/xoe-novai-foundation.git
 ! [remote rejected] feature/multi-account-hardening -> feature/multi-account-hardening (push declined due to repository rule violations)
error: failed to push some refs to 'https://github.com/Xoe-NovAi/xoe-novai-foundation.git'