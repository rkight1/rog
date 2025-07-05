{{! -*- mode: html -*- }}
{{> head }}
    <h1>{{page.title}}</h1>
    <ul>
    {{#page.collection}}
    <li><a href="{{url}}">{{title}}</a></li>
    {{/page.collection}}
    </ul>

{{> tail }}
