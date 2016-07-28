function updateCounts() {
  $(".heatCount").html("0");
  $(".heatSelector").each(function() {
    heat = $( this ).find(":selected").val();
    heatCount = $("#" + heat);
    if (heatCount) {
      heatCount.html(parseInt(heatCount.html()) + 1);
    }
  });
}

$(".heatSelector").change(updateCounts);

updateCounts();
