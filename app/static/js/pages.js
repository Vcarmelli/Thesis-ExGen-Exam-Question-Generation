document.addEventListener('DOMContentLoaded', () => {
    const selectedPagesInput = document.getElementById('selected-pages');
    const thumbnails = document.querySelectorAll('.thumbnail-item');
    const pageNumInput = document.getElementById('page-num');

    let selectedPages = new Set();

    // Function to format pages into a range string
    function formatPageRanges(pages) {
        const sortedPages = Array.from(pages).sort((a, b) => a - b);
        if (sortedPages.length === 0) return '';

        let ranges = [];
        let start = sortedPages[0];
        let end = start;

        for (let i = 1; i < sortedPages.length; i++) {
            if (sortedPages[i] === end + 1) {
                end = sortedPages[i];
            } else {
                ranges.push(start === end ? `${start}` : `${start}-${end}`);
                start = end = sortedPages[i];
            }
        }
        ranges.push(start === end ? `${start}` : `${start}-${end}`);
        return ranges.join(', ');
    }

    // Update the displayed input fields
    function updateInputs() {
        const formattedPages = formatPageRanges(selectedPages);
        selectedPagesInput.value = formattedPages;
        pageNumInput.value = formattedPages;
    }

    // Handle thumbnail clicks
    thumbnails.forEach((thumbnail, index) => {
        const pageIndex = index + 1;

        thumbnail.addEventListener('click', () => {
            if (selectedPages.has(pageIndex)) {
                selectedPages.delete(pageIndex);
                thumbnail.classList.remove('selected');
            } else {
                selectedPages.add(pageIndex);
                thumbnail.classList.add('selected');
            }
            updateInputs();
        });
    });

    // Handle manual page number input
    pageNumInput.addEventListener('input', () => {
        const pageNumbers = pageNumInput.value
            .split(',')
            .map(num => num.trim())
            .filter(num => num.match(/^\d+(-\d+)?$/));

        selectedPages.clear();

        pageNumbers.forEach(range => {
            const [start, end] = range.split('-').map(Number);
            if (!isNaN(start)) {
                if (!end || end < start) {
                    selectedPages.add(start);
                } else {
                    for (let i = start; i <= end; i++) {
                        selectedPages.add(i);
                    }
                }
            }
        });

        // Update selected thumbnail highlights
        thumbnails.forEach((thumbnail, index) => {
            const pageIndex = index + 1;
            if (selectedPages.has(pageIndex)) {
                thumbnail.classList.add('selected');
            } else {
                thumbnail.classList.remove('selected');
            }
        });

        updateInputs();
    });
});