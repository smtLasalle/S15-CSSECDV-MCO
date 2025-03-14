const tabBtn=document.querySelectorAll(".tab");
    const tab=document.querySelectorAll(".info");

    function tabs(index) {
        tabBtn.forEach(function (button, i) {
            if (i === index) {
                button.classList.add("active");
            } else {
                button.classList.remove("active");
            }
        });

        tab.forEach(function (node, i) {
            if (i === index) {
                node.style.display="block";
            } else {
                node.style.display="none";
            }
        });
    }

    // Initialize the first tab as active
    tabs(0);

    // Add event listeners to tab buttons
    tabBtn.forEach(function (button, index) {
        button.addEventListener('click', function () {
            tabs(index);
        });
    });