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
        fetch('quotes_data.json.md')
            .then(response => response.text()) // 텍스트로 받아서 마크다운 코드 블록 제거
            .then(text => {
                console.log('Fetch successful, processing text.'); // Step 1: Confirm .then is reached
                const jsonString = text.replace(/```json|```/g, ''); // 마크다운 코드 블록 제거
                console.log('JSON string after regex:', jsonString); // Step 2: Check jsonString
                const quotes = JSON.parse(jsonString);
                console.log('Parsed quotes object:', quotes); // Step 3: Check parsed quotes
                const todaysQuote = getTodaysQuote(quotes);
                console.log('Today\'s quote object:', todaysQuote); // Step 4: Check today's quote

                // HTML 요소에 명언 데이터 적용
                const quoteElement = document.querySelector('.quote');
                const sourceElement = document.querySelector('.source');
                const imageIdeaElement = document.querySelector('.image-idea p');
                const shortThoughtElement = document.querySelector('.short-thought p');
                const suggestedActionElement = document.querySelector('.suggested-action p');

                console.log('Quote element:', quoteElement); // Step 5: Check if elements are found
                console.log('Source element:', sourceElement);
                console.log('Image idea element:', imageIdeaElement);
                console.log('Short thought element:', shortThoughtElement);
                console.log('Suggested action element:', suggestedActionElement);

                if (quoteElement) quoteElement.textContent = todaysQuote.quote;
                if (sourceElement) sourceElement.textContent = todaysQuote.source;
                if (imageIdeaElement) imageIdeaElement.textContent = todaysQuote.image_idea;
                if (shortThoughtElement) shortThoughtElement.textContent = todaysQuote.short_thought;
                if (suggestedActionElement) suggestedActionElement.textContent = todaysQuote.suggested_action;

                // console.log('quotes:', quotes); // JSON 데이터 확인
                // console.log('todaysQuote:', todaysQuote); // 선택된 명언 확인

                // 초기에 모든 섹션을 보이도록 설정 (스크롤 스냅은 CSS로 처리)
                const sections = document.querySelectorAll('.section');
                sections.forEach(section => {
                    section.classList.add('visible');
                });

            })
            .catch(error => console.error('Error loading quotes:', error));
    }

    loadQuotes();

    // 스크롤 스냅 효과는 CSS로 처리하므로, JavaScript의 스크롤 관련 로직은
    // 더 정교한 제어가 필요할 때 추가하거나, fullPage.js 같은 라이브러리 사용을 고려합니다.
    // 현재는 CSS의 scroll-snap-type 과 scroll-snap-align 을 사용합니다.
    // 따라서 checkSlidesVisibility 함수와 관련 이벤트 리스너는 제거하거나 주석 처리합니다.

    /*
    function checkSlidesVisibility() {
        const sections = document.querySelectorAll('.section'); // .slide 대신 .section 사용
        const sectionContainer = document.querySelector('.section-container');
        if (!sectionContainer) return;

        sections.forEach(section => {
            const sectionTop = section.getBoundingClientRect().top - sectionContainer.getBoundingClientRect().top;
            const containerHeight = sectionContainer.clientHeight;

            // 섹션이 section-container 내에서 얼마나 보이는지 계산
            if (sectionTop < containerHeight * 0.8 && sectionTop + section.clientHeight > containerHeight * 0.2) {
                section.classList.add('visible');
            } else {
                // 화면 밖으로 나간 섹션은 다시 안보이게 할 수도 있음 (선택 사항)
                // section.classList.remove('visible');
            }
        });
    }

    const sectionContainer = document.querySelector('.section-container');
    if (sectionContainer) {
        sectionContainer.addEventListener('scroll', checkSlidesVisibility);
        window.addEventListener('load', () => {
            checkSlidesVisibility(); // 페이지 로드 시에도 실행
        });
    }
    */
});
