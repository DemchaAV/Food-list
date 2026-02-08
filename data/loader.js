// Scott's Food List - Data Loader
// Similar to Cocktail Trainer's loader.js

(function () {
    'use strict';

    window.allFoodItems = [];
    window.foodDataReady = false;

    // Category file mapping
    const categoryFiles = [
        'data/categories/scotts.js'
    ];

    let loadedCount = 0;

    function checkAllLoaded() {
        loadedCount++;
        if (loadedCount >= categoryFiles.length) {
            // All files loaded, dispatch event
            window.foodDataReady = true;
            window.dispatchEvent(new CustomEvent('foodLoaded'));
        }
    }

    // Register callback for category data
    window.registerFoodCategory = function (data) {
        if (Array.isArray(data)) {
            window.allFoodItems = window.allFoodItems.concat(data);
        }
        checkAllLoaded();
    };

    // Load all category scripts
    categoryFiles.forEach(file => {
        const script = document.createElement('script');
        script.src = file;
        script.async = false;
        script.onerror = () => {
            console.error('Failed to load:', file);
            checkAllLoaded();
        };
        document.head.appendChild(script);
    });
})();
