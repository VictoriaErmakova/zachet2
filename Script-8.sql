create table tasks(
id serial primary key,
description text not null,
priority varchar(50) check (priority in ('высокий', 'средний','низкий')),
completed boolean default false);