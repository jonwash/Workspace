# Fruit Merge

A Suika-style fruit merge game with levels, in a single self-contained HTML file — no dependencies, no build step.

**Play:** open `index.html` in any browser.

## How to play

- Each level starts pre-filled with fruit raining into the tray, then gives you a **move budget** and a **goal fruit** (shown top-right).
- Move the mouse (or drag on touch) to aim — a ghost ring previews where the fruit will land — then click/tap to drop. Keyboard: ←/→ to aim, Space or ↓ to drop.
- Two touching fruits of the same kind pull together and pop into the next bigger fruit.
- Eleven tiers: cherry → strawberry → grape → dekopon → orange → apple → pear → peach → pineapple → melon → watermelon. Merging two watermelons clears them for a +200 bonus.
- Make the goal fruit before the move counter hits zero to clear the level; leftover moves pay a bonus. Later levels demand bigger fruits with denser pre-fills.
- Running out of moves — or letting the pile rest above the dashed red line — fails the level; tap to retry it. Best score and best level are saved locally.
