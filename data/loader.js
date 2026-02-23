// Scott's Food List - Data Loader
// Supports current + previous menu versions

(function () {
    'use strict';

    window.allFoodItems = [];
    window.previousFoodItems = [];
    window.foodDataReady = false;

    // Current menu files
    const categoryFiles = [
        'data/categories/scotts.js'
    ];

    // Previous menu files
    const previousFiles = [
        'data/categories/scotts_previous.js'
    ];

    let loadedCount = 0;
    const totalFiles = categoryFiles.length + previousFiles.length;

    function checkAllLoaded() {
        loadedCount++;
        if (loadedCount >= totalFiles) {
            window.foodDataReady = true;
            window.dispatchEvent(new CustomEvent('foodLoaded'));
        }
    }

    // Register callback for current menu data
    window.registerFoodCategory = function (data) {
        if (Array.isArray(data)) {
            window.allFoodItems = window.allFoodItems.concat(data);
        }
        checkAllLoaded();
    };

    // Register callback for previous menu data
    window.registerPreviousFoodCategory = function (data) {
        if (Array.isArray(data)) {
            window.previousFoodItems = window.previousFoodItems.concat(data);
        }
        checkAllLoaded();
    };

    // Load all scripts
    [...categoryFiles, ...previousFiles].forEach(file => {
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
