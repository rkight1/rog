{{! -*- mode: html -*- }}
{{> head }}
    <h1>Pages tagged <span class="title-tag-name">{{page.collectionName}}</span></h1>
    <ul>
    {{#page.collectionPages}}
    <li><a href="{{url}}">{{title}}</a></li>
    {{/page.collectionPages}}
    </ul>

{{> tail }}
