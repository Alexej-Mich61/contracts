// static/js/contract-form.js

function addAK() {
    const container = document.getElementById('ak-container');
    const totalForms = document.querySelector('#id_aks-TOTAL_FORMS');
    const formIdx = parseInt(totalForms.value);

    let newFormHtml = document.getElementById('empty-ak-form').innerHTML;
    newFormHtml = newFormHtml.replace(/__prefix__/g, formIdx);

    container.insertAdjacentHTML('beforeend', newFormHtml);
    totalForms.value = formIdx + 1;
}