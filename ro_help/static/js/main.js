document.addEventListener("DOMContentLoaded", () => {
  // Get all "navbar-burger" elements
  const $navbarBurgers = Array.prototype.slice.call(
    document.querySelectorAll(".navbar-burger"),
    0
  );

  // Check if there are any navbar burgers
  if ($navbarBurgers.length > 0) {
    // Add a click event on each of them
    $navbarBurgers.forEach((el) => {
      el.addEventListener("click", () => {
        // Get the target from the "data-target" attribute
        const target = el.dataset.target;
        const $target = document.getElementById(target);

        // Toggle the "is-active" class on both the "navbar-burger" and the "navbar-menu"
        el.classList.toggle("is-active");
        $target.classList.toggle("is-active");
      });
    });
  }

  // registration city select lazy load
  const countySelect = $("#id_county");
  const citySelect = $("#id_city");

  countySelect.change(async function () {
    const cityResponse = await fetch(
      `${citySelect.data("url")}?county=${this.value}`
    );
    const cityList = await cityResponse.json();

    const cityHtml = [];
    citySelect.empty();
    $.each(cityList, function (_, value) {
      cityHtml.push(`<option value=${value.id}>${value.city}</option>`);
    });
    citySelect.append(cityHtml);
    citySelect.attr("disabled", false);
  });
});
