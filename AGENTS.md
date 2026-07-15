# Ring Fountain project rules

1. Work only in WSL2 Ubuntu and keep the project under `/home/kqdx/basilisk_work/ring_fountain`.
2. Treat `/home/kqdx/basilisk` and `/home/kqdx/basilisk/src` as read-only.
3. `/home/kqdx/basilisk/src/qcc` is the final compilation authority.
4. VS Code IntelliSense diagnostics do not override a `qcc` result.
5. Keep third-party source read-only and inspect its license before use.
6. Do not copy GPL code into this project unless the project license decision explicitly permits it.
7. Preserve copyright and license notices when copying MIT code.
8. Compile and run every version that is claimed to work.
9. Do not claim success from an animation alone; record numerical diagnostics.
10. Record mass conservation, maximum velocity, time step, and cell counts for dynamic cases.
11. Never overwrite historical results in `runs/`.
12. Keep each stage independently reviewable and commit it when Git storage is available.
13. Update `docs/HANDOFF.md` every work round.
14. Do not enter a later physics stage before its validation gate passes.
15. Never read, copy, print, upload, commit, or regenerate SSH private keys.
16. Never push to a remote repository automatically.

