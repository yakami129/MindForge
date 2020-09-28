export const booleanRenderer = (params) => {
    const toggle = (e) => {
        params.value = !params.value
        params.setValue(e.currentTarget.checked)
    }
    let input = document.createElement("input")
    input.type = "checkbox"
    input.checked = params.value
    input.addEventListener("click", toggle)

    return input
}