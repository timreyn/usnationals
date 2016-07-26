function updateCounts() {
  $(".heatCount").html("0");
  $(".heatSelector").each(function() {
    heat = $( this ).find(":selected").name;
    heatCount = $("#" + heat);
    if (heatCount) {
      heatCount.html(parseInt(heatCount.html()) + 1);
    }
  });
}

$(".heatselector").change(updateCounts);

updateCounts();
