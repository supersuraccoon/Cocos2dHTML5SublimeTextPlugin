// Created By Cocos2dHtml5Dev plugin

var TemplateLayer = cc.Layer.extend({
    ctor:function() {
        this._super();
        cc.associateWithNative( this, cc.Layer );
    },
    init:function () {
        return true;
    }
});

var TemplateScene = cc.Scene.extend({
    onEnter:function () {
        this._super();
        var layer = new TemplateLayer();
        layer.init();
        this.addChild(layer);
    }
});

