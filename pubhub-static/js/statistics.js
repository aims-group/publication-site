data = Bind({
  // data
  name: '',
  list: []
}, {
  // bind mapping
  name: '#click-id',
  list: {
    dom: '#click-stats',
    transform: function (obj) {
        return '<li class="list-group-item">' + this.safe(obj.name) + '<span class="badge">' + this.safe(obj.count) + '</span></li>';
    },
  }
});