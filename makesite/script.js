document.addEventListener('DOMContentLoaded', function() {
    // 오늘 날짜를 기준으로 명언을 선택하는 함수
    function getTodaysQuote(quotes) {
        const today = new Date();
        const dayOfYear = Math.floor((today - new Date(today.getFullYear(), 0, 0)) / (1000 * 60 * 60 * 24));
        const index = (dayOfYear - 1) % quotes.length; // day_number는 1부터 시작하므로 1을 빼줌
        return quotes[index];
    }

    // JSON 데이터를 가져오는 함수
    function loadQuotes() {
        fetch('makesite/quotes_data.json.md')
            .then(response => response.text()) // 텍스트로 받아서 마크다운 코드 블록 제거
            .then(text => {
                const jsonString = text.replace(/```json|```/g, ''); // 마크다운 코드 블록 제거
                const quotes = JSON.parse(jsonString);
                const todaysQuote = getTodaysQuote(quotes);

                // HTML 요소에 명언 데이터 적용
                document.querySelector('.quote').textContent = todaysQuote.quote;
                document.querySelector('.source').textContent = todaysQuote.source;

                // 슬라이드 효과를 위한 코드
                const slideContainer = document.querySelector('.slide-container');
                const slides = slideContainer.querySelectorAll('.slide');
                slides.forEach((slide, index) => {
                    setTimeout(() => {
                        slide.classList.add('active');
                    }, 500 * (index + 1)); // 0.5초 간격으로 순차적으로 나타나도록 설정
                });

                document.querySelector('.image-idea p').textContent = '이미지 컨셉: ' + todaysQuote.image_idea;
                document.querySelector('.short-thought p').textContent = '짧은 생각/해설: ' + todaysQuote.short_thought;
                document.querySelector('.suggested-action p').textContent = '추천 행동: ' + todaysQuote.suggested_action;
            })
            .catch(error => console.error('Error loading quotes:', error));
    }

    loadQuotes();
});