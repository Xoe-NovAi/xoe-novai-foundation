# How to Adjust `run_shell_command` Timeout in Gemini CLI

**IMPORTANT UPDATE**: After extensive internal research, it has been determined that **there is currently no explicit user-configurable setting to adjust the timeout for the `run_shell_command` tool within this Gemini CLI environment.**

The timeouts experienced during `run_shell_command` executions are imposed by the underlying execution environment or the tool executor's internal, non-configurable limits. My previous advice regarding modifying configuration files or environment variables was based on general CLI tool practices and does not apply to this specific Gemini CLI implementation. I apologize for any misdirection caused by this oversight.

---

## What This Means for You:

*   You cannot directly increase the timeout limit for `run_shell_command` through configuration files or environment variables.
*   We must find alternative strategies to ensure long-running shell commands complete successfully within the existing, non-configurable timeout.

## Strategies to Mitigate Timeouts:

Given that the timeout cannot be adjusted, we must focus on making the build process faster or breaking it down into smaller, self-contained steps.

1.  **Optimize Build Process**:
    *   **Local Caching (`apt-cacher-ng`)**: Resolve the issues with `apt-cacher-ng` to significantly speed up Debian package downloads. This is now paramount.
    *   **BuildKit Cache**: Ensure BuildKit cache mounts are fully effective for both APT and Python package installations to minimize repeated work.
2.  **Break Down Long Commands**: If a single command exceeds the timeout, it might be possible to split it into multiple smaller commands.
3.  **Background Processes**: For commands that can run independently, consider running them in the background if the task allows (though this requires careful management of their lifecycle).

---

## Re-prioritizing the Path Forward:

Since we cannot extend the timeout, making the build process itself more efficient becomes the immediate and critical priority. This means we must resolve the `apt-cacher-ng` port conflict.

**Immediate Action**: We must troubleshoot and resolve the persistent port binding issue preventing `apt-cacher-ng` from starting. Once `apt-cacher-ng` is operational, it should significantly reduce Debian package download times, allowing the overall build process to complete within the existing timeout limits.

---

I apologize again for the previous incorrect guidance. We will now focus on resolving the `apt-cacher-ng` issue as the primary means to overcome the build timeouts.