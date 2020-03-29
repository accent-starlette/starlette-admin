import json

from wtforms import widgets


class CheckboxInput(widgets.CheckboxInput):
    def __call__(self, field, **kwargs):
        rendered_field = super().__call__(field, **kwargs)
        return widgets.HTMLString(
            """
            %s<label class="state" for="%s">&nbsp;</label>
            """
            % (rendered_field, field.id)
        )


class FileInput(widgets.FileInput):
    def __call__(self, field, **kwargs):
        kwargs.update(
            {"@change": "count = $event.target.files.length", "class": "d-hidden"}
        )
        rendered_field = super().__call__(field, **kwargs)
        return widgets.HTMLString(
            """
            <label x-data="{count: 0}" class="file-field input-group">
                <div class="info" x-text="count ? count + ' files(s) selected' : 'Choose file(s)'"></div>
                %s
                <span class="button button-secondary input-group-addon">Browse</span>
            </label>
            """
            % rendered_field
        )


class HorizontalSelect(widgets.Select):
    def __init__(self):
        self.multiple = True

    def __call__(self, field, **kwargs):
        kwargs.update(
            {"x-ref": "field", "class": "d-hidden", "@change": "ev = $event.timeStamp"}
        )
        rendered_field = super().__call__(field, **kwargs)
        return widgets.HTMLString(
            """
            <div class="select-multi-field"
                x-data="{ ev: null }"
                @set-one="
                    $refs.field.options[$event.detail.key].selected = $event.detail.selected;
                    $dispatch('propagate');
                "
                @set-all="
                    Object.keys($refs.field.options).forEach(key => $refs.field.options[key].selected = $event.detail);
                    $dispatch('propagate');
                "
                @propagate="$refs.field.dispatchEvent(new Event('change'))"
            >
                %s
                <div class="row">
                    <div class="col-12 col-sm-6 col-md-5 col-lg-4">
                        <div class="title">
                            <a href="#" class="pull-right" @click.prevent="$dispatch('set-all', true)">Choose all</a>
                            Available
                        </div>
                        <ul>
                            <template x-for="key in Object.keys($refs.field.options)" :key="key">
                                <li x-show="!$refs.field.options[key].selected">
                                    <a href="#"
                                        @click.prevent="$dispatch('set-one', {key, selected: true})"
                                        x-text="$refs.field.options[key].label"
                                    ></a>
                                </li>
                            </template>
                        </ul>
                    </div>
                    <div class="col-12 col-sm-6 col-md-5 col-lg-4">
                        <div class="title">
                            <a href="#" class="pull-right" @click.prevent="$dispatch('set-all', false)">Remove all</a>
                            Selected
                        </div>
                        <ul>
                            <template x-for="key in Object.keys($refs.field.options)" :key="key">
                                <li x-show="$refs.field.options[key].selected">
                                    <a href="#"
                                        @click.prevent="$dispatch('set-one', {key, selected: false})"
                                        x-text="$refs.field.options[key].label"
                                    ></a>
                                </li>
                            </template>
                        </ul>
                    </div>
                </div>
            </div>
            """
            % rendered_field
        )


class PasswordInput(widgets.PasswordInput):
    def __call__(self, field, **kwargs):
        kwargs.update({":type": "show ? 'text' : 'password'"})
        rendered_field = super().__call__(field, **kwargs)
        return widgets.HTMLString(
            """
            <div class="password-field icon-input" x-data="{ show: false }">
                %s
                <span class="fa" :class="{'fa-eye': !show, 'fa-eye-slash': show}" @click="show = !show"></span>
            </div>
            """
            % rendered_field
        )


class RadioInput(widgets.RadioInput):
    def __call__(self, field, **kwargs):
        rendered_field = super().__call__(field, **kwargs)
        return widgets.HTMLString(
            """
            %s<label class="state" for="%s">&nbsp;</label>
            """
            % (rendered_field, field.id)
        )


class Select(widgets.Select):
    def __call__(self, field, **kwargs):
        rendered_field = super().__call__(field, **kwargs)
        return widgets.HTMLString(
            """
            <div class="select-field icon-input">
                %s
                <span class="fa fa-caret-down"></span>
            </div>
            """
            % rendered_field
        )


class TagsInput(widgets.TextInput):
    def __call__(self, field, **kwargs):
        kwargs.update({":value": "JSON.stringify(tags)", "class": "d-hidden"})
        rendered_field = super().__call__(field, **kwargs)
        return widgets.HTMLString(
            """
            <div x-data='{ tags: %s, newTag: "" }'>
                %s
                <div class="tags-field">
                    <template x-for="tag in tags" :key="tag">
                        <span class="tag">
                            <span x-text="tag"></span>
                            <a href="#"
                                @click.prevent="tags = tags.filter(i => i !== tag)">
                                <i class="fa fa-times"></i>
                            </a>
                        </span>
                    </template>
                    <input placeholder="add a new tag ..."
                        x-model="newTag"
                        @keydown.enter.prevent="
                            if (newTag.trim() !== ''
                                && tags.indexOf(newTag.trim()) == -1
                            ) tags.push(newTag.trim()); newTag = ''"
                        @keydown.backspace="if (newTag === '') tags.pop()"
                    >
                </div>
            </div>
            """
            % (json.dumps(field.data), rendered_field)
        )
