var get_group_status = function(stage) {
  return function() {
    $.ajax({
      type: "get",
      url: "/current_group/" + stage.substring(0, 1),
    }).done(function(data) {
      if (data.current_group) {
        $("#" + stage + " > .current > .icon").html("<img src='/static/img/e_" + data.current_group.round.event.id + ".png'></img>");
        $("#" + stage + " > .current > .eventname").html(data.current_group.number);
      } else {
        $("#" + stage + " > .current > .icon").html("");
        $("#" + stage + " > .current > .eventname").html("");
      }
      if (data.next_group) {
        $("#" + stage + " > .nextevent > .icon").html("<img src='/static/img/e_" + data.next_group.group.round.event.id + ".png'></img>");
        $("#" + stage + " > .nextevent > .eventname").html(data.next_group.group.number + " (" + data.next_group.estimate + ")");
      } else {
        $("#" + stage + " > .nextevent > .icon").html("");
        $("#" + stage + " > .nextevent > .eventname").html("");
      }
    });
  };
}

setInterval(get_group_status('r'), 30000);
setInterval(get_group_status('b'), 30000);
setInterval(get_group_status('g'), 30000);
setInterval(get_group_status('o'), 30000);
setInterval(get_group_status('y'), 30000);

get_group_status('r')();
get_group_status('b')();
get_group_status('g')();
get_group_status('o')();
get_group_status('y')();
