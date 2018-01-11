window.onload = function () {
    Vue.filter('get_menu_ico_path', function (value) {
        if (value && value.indexOf(',') > 0) {
            var menu_path = value.split(',')
            return "/" + menu_path[0] + '/' + menu_path[1];
        }
    });
    Vue.filter('menu_to_link', function (value) {
        return "/second/nemu/" + value.id;
    });
    Vue.filter('obj_str_to_id', function (value) {
        if (value && value.indexOf(',') > 0) {
            var menu_path = value.split(',')
            return menu_path[1];
        }
    });
    Vue.filter('format_data', function (value) {
        if(value){
            return value
        }else{
            return ''
        }

    });
    Vue.directive("longtouch", function (el, binding) { //自定义 长按 弹出菜单选项
        var oDiv = el,
            value = binding.value,
            x = 0, y = 0, z = 0, timer = null;
        oDiv.addEventListener("touchstart", function (e) {
            if (e.touches.length > 1) {
                return false;
            }
            z = 0;
            timer = setTimeout(function () {
                z = 1;
            }, 500);
            x = e.touches[0].clientX;
            y = e.touches[0].clientY;
            e.preventDefault();
        }, false);
        document.addEventListener("touchmove", function (e) {
            if (x != e.touches[0].clientX || y != e.touches[0].clientY) {
                clearTimeout(timer);
                return false;
            }
        }, false);
        document.addEventListener("touchend", function (ev) {
            if (z != 1) {
                clearTimeout(timer);
                x = 0;
                y = 0;
                return false;
            } else {
                x = 0;
                y = 0;
                z = 0;
                if (value.length > 0) {
                    $.actions({
                        onClose: function () {
                        },
                        actions: value
                    })
                }
            }
        }, false);
    });
    Vue.filter('length', function (value) {
        if (value == null) return 0;
        if (typeof value != "string") {
            value += "";
        }
        return value.replace(/[^\x00-\xff]/g, "01").length;
    });

    Vue.component('mobileViews', {
            props: ['all_field', 'all_record_data', 'show_views', 'field_views', 'view_type'],
            template: "#mobile_tree_component",
            computed: {},
            data: function () {
              return {
                  one_record_data: '',
                  component_all_field:this.all_field,
                  component_all_record_data:this.all_field,
                  component_show_views:this.show_views,
                  component_field_views:this.field_views,
                  component_view_type:this.view_type
              }
            },
            methods: {
                click_cell: function (row, column, cell, event) {
                    //单击某一行事件
                    if (column.type == 'default' && column.label != '操作') {
                        if (this.$children[0].selection) {
                            $.actions({
                                onClose: function () {
                                },
                                actions: [{
                                    text: "删除",
                                    className: 'color-danger',
                                    onClick: function () {
                                        $.toast("删除成功!");
                                    }
                                }]
                            })
                        }
                    }
                },
                row_select: function (selection, row) {
                    //选中事件
                    console.log(selection);
                    console.log("+++++++++++++++++++");
                },
                handleEdit: function (index, row) {
                    this.component_view_type='form';
                    this.one_record_data = row;
                    console.log(row);
                    console.log(this.show_views);
                    console.log(this.all_field);
                    console.log( this.view_type);
                }
            },
            watch: {
                // 如果 question 发生改变，这个函数就会运行
                component_all_field: function (newvalue) {
                    this.$emit('update:all_field', newvalue)
                },
                component_all_record_data: function (newvalue) {
                    this.$emit('update:all_record_data', newvalue)
                },
                component_show_views: function (newvalue) {
                    this.$emit('update:show_views', newvalue)
                },
                component_field_views: function (newvalue) {
                    this.$emit('update:field_views', newvalue)
                },
                component_view_type: function (newvalue) {
                    console.log(newvalue);
                    this.$emit('update:view_type', newvalue)
                },
            }
        }
    );
    const actionManager = {
        template: '#mobile_action_view',
        data: function () {
            return {
                field_views: [],
                show_views: [],
                all_field: [],
                all_record_data: [],
                ele_table_height: 400,
                view_type: 'tree',
                form_fields: [],
                // show_view_type:'list',
            }
        },
        created: function () {
            this.$parent.show_first_level_menu = false;
            this.get_view_data();
        },
        watch: {
            '$route': function (to, from) {

                this.get_view_data();
            }
        },
        methods: {
            get_view_data: function (action) {
                var search_read_url = '/mobile/search_read';
                var all_field_url = '/mobile/fields_get';
                var load_view_url = '/mobile/load_views';
                var url = "/mobile/action/load";
                this.view_type = 'tree';
                this.$http.get(url, {params: {action_id: this.$route.params.action_id}}).then(function (res) {
                    var current_action = res.body
                    if (current_action) {
                        if (!current_action.views) {
                            this.$notify.error({
                                title: '错误',
                                message: '这个菜单对应的动作没有定义视图类型！'
                            });
                        }
                        this.$http.get(load_view_url, {
                            params: {
                                model: current_action.res_model,
                                views: JSON.stringify(current_action.views),
                            }
                        }).then(function (res) {
                            this.field_views = res.body;
                            this.xml_convert_to_json(this.field_views)
                        });
                        this.$http.get(all_field_url, {params: {model: current_action.res_model}}).then(function (res) {
                            this.all_field = res.body;
                            console.log(this.all_field);

                        });
                        this.$http.get(search_read_url, {params: {model: current_action.res_model}}).then(function (res) {
                            this.all_record_data = res.body;
                            console.log(this.all_record_data);
                        });
                    }
                });
            },
            get_all_field:function (form) {
                for(xml_tag in form){
                    if(xml_tag=='field'){
                        if(Array.isArray(form[xml_tag])){
                            this.show_views.form.push.apply(this.show_views.form, form[xml_tag]);
                        }else{
                            this.show_views.form.push(form[xml_tag])
                        }

                    }else if(typeof form[xml_tag]=='object'){
                        this.get_all_field(form[xml_tag])
                    }
                }
            },
            xml_convert_to_json: function (field_views) {
                for (view in field_views.fields_views) {
                    var x2js = new X2JS();
                    var viewJsonObj = x2js.xml_str2json(field_views.fields_views[view].arch);
                    field_views.fields_views[view].arch_jsonobj = viewJsonObj;
                    if (view == 'list') {
                        this.show_views.tree = viewJsonObj.tree;
                        //console.log(this.show_views)
                    }else if(view == 'form'){
                        console.log(viewJsonObj);
                        this.show_views.form = [];
                        this.get_all_field(viewJsonObj.form);//列表中有对象有 列表对象 还需要进一步的

                        console.log(this.form_fields);
                        console.log( 'this.form_fields');
                    }
                }
            },
        }
    };

    const routes = [
        {path: '/action/:action_id', component: actionManager, name: 'action'},
    ]
    const router = new VueRouter({
        routes: routes // （缩写）相当于 routes: routes
    });
    const app = new Vue({
        router: router,
        data: function () {
            return {
                active_second_view_id: '',
                first_level_menu: [],
                second_level_menu: [],
                last_leve_menu: [],
                show_first_level_menu: true,
                current_action: '',
            }
        },
        created: function () {
            var url = "/odoo/get_first_level_menu";
            this.$http.get(url).then(function (res) {
                this.first_level_menu = res.body;
            });
        },
        methods: {
            onclick_first_level_menu: function (menu_id) {
                var url = "/odoo/get_second_level_menu";
                this.$http.get(url, {params: {parent_id: menu_id}}).then(function (res) {
                    if (res.body) {
                        this.show_first_level_menu = false;
                        this.second_level_menu = res.body;
                        if (res.body && typeof res.body == 'object' && res.body[0]) {
                            this.active_second_view_id = this.second_level_menu[0].id;
                        }
                    }
                });
            },
            onclick_second_level_menu: function (menu_id) {
                var url = "/odoo/get_last_level_menu";
                this.active_second_view_id = menu_id;
                this.$http.get(url, {params: {parent_id: menu_id}}).then(function (res) {
                    if (res.body) {
                        this.last_leve_menu = res.body;
                    }
                });
            },
            onclick_last_level_menu: function (action_id) {
                if (action_id && action_id.indexOf(',')) {
                    action_id = action_id.split(',')[1];
                    this.$router.push({name: 'action', params: {action_id: action_id}});
                }
            }
        },
        watch: {
            second_level_menu: function (newVal, oldVal) {
                var url = "/odoo/get_last_level_menu";
                if (newVal && typeof newVal == 'object' && newVal[0]) {
                    menu_id = newVal[0].id;
                    this.$http.get(url, {params: {parent_id: menu_id}}).then(function (res) {
                        this.last_leve_menu = res.body;
                    });
                }
            },
            active_second_view_id: function (newVal, oldVal) {
                if (newVal != oldVal) {
                    $("#second_menu_" + newVal).addClass('weui-state-active');
                    $("#second_menu_" + oldVal).removeClass('weui-state-active');
                }

            },
        },
    }).$mount('#app');
}
;

