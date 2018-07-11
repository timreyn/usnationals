function updateCounts() {
  $(".groupCount").html("0");
  $(".groupSelector").each(function() {
    group = $( this ).find(":selected").val();
    groupCount = $("#" + group);
    if (groupCount) {
      groupCount.html(parseInt(groupCount.html()) + 1);
    }
  });
}

$(".groupSelector").change(updateCounts);

updateCounts();
