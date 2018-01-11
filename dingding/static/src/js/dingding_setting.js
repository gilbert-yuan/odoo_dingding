window.onload = function () {
   /* dd.error(function (err) {
        alert('dd error: ' + JSON.stringify(err));
    });
    dd.ready(function () {
        dd.biz.navigation.setTitle({
            title: '钉钉demo',
            onSuccess: function (data) {

            },
            onFail: function (err) {
                log.e(JSON.stringify(err));
            }
        });
        dd.runtime.info({
            onSuccess: function (info) {

            },
            onFail: function (err) {
                alert('fail: ' + JSON.stringify(err));
            }
        });
        dd.runtime.permission.requestAuthCode({
            corpId: corpid,
            onSuccess: function (result) {
                var code = result.code;
                $.ajax({
                    url: "/get_user_info?access_token=" + accesstoken + "&code=" + code,
                    method: "GET",
                }).then(function (data) {*/
                    const notFound = {
                        template: '#test_scroller'
                    };

                    const toast_success = {
                        props: {success_msg: String},
                        template: '#toast_success',
                        data: function () {
                            return {success_msg: 'hello'}
                        },
                    };

                    Vue.component('toast-success', toast_success);
                    Vue.filter('length', function (value) {
                        if (value == null) return 0;
                        if (typeof value != "string") {
                            value += "";
                        }
                        return value.replace(/[^\x00-\xff]/g, "01").length;
                    });

                    const gridsViews = {
                        //props: ['img_src', 'new_page', 'show_str'],
                        template: '#vue_grid',
                        // 技术上 data 的确是一个函数了，因此 Vue 不会警告，
                        // 但是我们返回给每个组件的实例的却引用了同一个data对象
                        data: function () {
                            return {
                                all_grid: [{
                                    new_page: "new_ask_for_leave",
                                    link: {'path': '/allopereation/treeFormView'},
                                    img_src: "/dingding/static/src/img/sale.png",
                                    type: 'work',
                                    show_str: '销售订单',
                                },
                                ]
                            }
                        },
                    };
                    Vue.component('vue_input_val', {
                        props: ['required', 'value', 'pattern', 'str', 'disabled', 'type_detail', 'required_error'],
                        template: "#vue_input_component",
                        data: function () {
                            return {

                                input_required: this.required,
                                input_pattern: this.pattern,
                                input_str: this.str,
                                input_disabled: this.disabled,
                                input_type_detail: this.type_detail,
                                input_required_error: this.required_error,
                            };
                        },
                        computed: {
                            input_value: {
                                get: function () {
                                    return this.value
                                },
                                set: function (v) {
                                    this.$emit('update:value', v);

                                }
                            }
                        },
                        watch: {
                            // 如果 question 发生改变，这个函数就会运行
                            input_required: function (newvalue) {
                                this.$emit('update:required', newvalue)
                            },
                            input_type_detail: function (newvalue) {
                                this.$emit('update:type_detail', newvalue)
                            },
                            input_disabled: function (newvalue) {
                                this.$emit('update:disabled', newvalue)
                            },
                            input_pattern: function (newvalue) {
                                this.$emit('update:pattern', newvalue)
                            },
                            input_str: function (newvalue) {
                                this.$emit('update:str', newvalue)
                            },
                            input_required_error: function (newvalue) {
                                this.$emit('update:required_error', newvalue)
                            },
                        },
                    });
                    const treeFormView = {
                        template: '#vue_list_view',
                        data: function () {
                            return {
                                all_records: [],
                                all_label:[],
                                all_invisible: this.$route.query.approve_type,
                                success_msg: '',
                                loading: true,
                                offset: 0,
                                locading_msg: '加载数据中',
                                now_record_length: 0,
                                is_all_records_data: true,
                            }
                        },
                        created: function () {
                            this.get_all_records();
                        },
                        methods: {
                            get_all_records: function () {
                                var url = "/dingding/get_sale_order";
                                this.offset = 0;
                                this.$http.get(url, {
                                    params: {
                                        type: this.$route.query.type,
                                        unapprove: this.$route.query.approve_type,
                                        offset: this.offset,
                                    }
                                }).then(function (res) {
                                    this.now_record_length = res.body.length;
                                    this.all_records = res.body[0];
                                    this.all_label = res.body[1];
                                })
                            },
                            refresh: function (done) {
                                var self = this;
                                setTimeout(function () {
                                    self.get_all_records();
                                    done();
                                }, 500)
                            },
                            infinite: function (done) {
                                var self = this;
                                if (self.is_all_records_data || this.now_record_length < 4) {
                                    setTimeout(function () {
                                        done(true);
                                        self.is_all_records_data = false;
                                    }, 500)
                                    return;
                                }
                                setTimeout(function () {
                                    self.offset = self.offset + 4;
                                    var url = "/dingding/get_sale_order";
                                    self.$http.get(url, {
                                        params: {
                                            type: self.$route.query.type,
                                            unapprove: self.$route.query.approve_type,
                                            offset: self.offset,
                                        }
                                    }).then(function (res) {
                                        if (res.body.length != 4) {
                                            self.is_all_records_data = true;
                                        } else {
                                            self.is_all_records_data = false;
                                        }
                                        this.now_record_length = res.body.length
                                        self.all_records = self.all_records.concat(res.body);
                                    });
                                    self.bottom = self.bottom + 10;
                                    done();
                                }, 500)
                            }
                        },
                    };
                    const routes = [
                        {path: '*', component: notFound},
                        {path: '/', component: gridsViews},
                        {path: '/allopereation/treeFormView', component: treeFormView},
                        {path: '/allopereation/treeFormView', component: treeFormView},
                    ]
                    const router = new VueRouter({
                        routes: routes // （缩写）相当于 routes: routes
                    });
                    const app = new Vue({
                        router: router,
                    }).$mount('#app');

    //             });
    //         },
    //         onFail: function (err) {
    //             alert("-----" + JSON.stringify(err.code));
    //
    //         }
    //     })
    // });
}