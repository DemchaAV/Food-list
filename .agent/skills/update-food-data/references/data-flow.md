# Data Flow

## Loader inputs

- current menu: `data/categories/scotts.js`
- previous menu: `data/categories/scotts_previous.js`

## Runtime behavior

- `data/loader.js` loads both files
- current menu populates `window.allFoodItems`
- previous menu populates `window.previousFoodItems`
- UI pages can switch between current and previous menu views
