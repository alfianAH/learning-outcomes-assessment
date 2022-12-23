function targetPageOnChange(element) {
    let minPage = $(element).attr('min');
    let maxPage = $(element).attr('max');
    let submittedValue = $(element).val();

    let paramString = window.location.search.substring(1);;
    let queryString = new URLSearchParams(paramString);
    let currentPage = queryString.get('page');

    if (submittedValue < minPage || submittedValue > maxPage || currentPage == submittedValue) return;

    element.form.submit();
}