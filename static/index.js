document.addEventListener("DOMContentLoaded", function () {
    const dropdownTrigger = document.querySelector('.nav-item.dropdown > .nav-link');
    const dropdownMenu = document.querySelector('.nav-item.dropdown .dropdown-menu');

    dropdownTrigger.addEventListener("click", function () {
        dropdownMenu.classList.toggle('show');
    });

    // Close the dropdown when clicking outside of it
    document.addEventListener('click', function (event) {
        if (!dropdownTrigger.contains(event.target) && !dropdownMenu.contains(event.target)) {
            dropdownMenu.classList.remove('show');
        }
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const sliderInner = document.querySelector('.doctor-slider-inner');
    const sliderItems = document.querySelectorAll('.slider-item');
    const totalItems = sliderItems.length;
    const sliderWidth = sliderInner.offsetWidth;
    let currentIndex = 0;
    let scrollAmount = 0;
    const itemWidth = sliderItems[0].offsetWidth + 20; // Adjust 20 as per your margin between items

    function scrollSlider() {
        if (currentIndex >= totalItems - 1) {
            currentIndex = 0;
            scrollAmount = 0;
        } else {
            currentIndex++;
            scrollAmount += itemWidth;
        }

        sliderInner.scrollTo({ left: scrollAmount, behavior: 'smooth' });
    }

    setInterval(scrollSlider, 3000); // Change image every 3 seconds (adjust as needed)
});