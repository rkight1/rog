{{! -*- mode: html -*- }}
{{> head }}
    <h1>{{page.title}}</h1>
    <ul>
    {{#page.tagPages}}
    <li><a href="{{url}}">{{title}}</a></li>
    {{/page.tagPages}}
    </ul>

{{> tail }}
