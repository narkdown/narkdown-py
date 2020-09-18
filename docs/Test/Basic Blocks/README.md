# Basic Blocks

> ⚠️ [Notion2Github](https://github.com/younho9/notion2github) is a tool to use Notion as a [Github Flavored Markdown](https://github.github.com/gfm/)(a.k.a GFM) editor.
> So [Notion2Github](https://github.com/younho9/notion2github) Does not support all features that Notion has.

## Headings `Support`

> ☝ Notion has a title for the page, but it only supports headings up to step 3. On the other hand, GFM supports headings up to six steps. Therefore, when exporting a Notion page, you can use the title of the page as heading 1 and lower the rest by one level to support a total of four levels of heading.
> Also, remember that each page usually has only one title(heading 1).

### Heading 3

#### Heading 4

## Divider `Support`

> ☝ In [GFM](https://github.github.com/gfm/), the divider is automatically rendered after header 1 and 2, so the divider after the header is not added.

## Divider after Heading 2

### Divider after the other

---

## Text `Support`

> ☝ [You can see it from here in the table view.](https://www.notion.so/younho9/5fe91726673a4121933fa10ae46a253a?v=57957dae2d4c4a809957bf39a9aa8467)

This is plain text. `Support`

**This is bold text.** `Support`

_This text is italicized._ `Support`

`this text is inline code.` `Support`

~~This was mistaken text.~~ `Support`

**This text is** **_extremely_** **important.** `Support`

**_All this text is important._** `Support`

[this text is link.](https://github.com/younho9/notion2github) `Support`

This text has color. `Not Support`

This text has background color. `Not Support`

## Callout & Quote `Support`

> ☝ This is an example callout. **Callout block will be exported as quote block with emoji.**

> ✅ This is an example quote. **Quote block with emoji is same with callout block.**

## Bulleted list `Support`

> 🎉 [Notion2Github](https://github.com/younho9/notion2github) support nested block.

- Bullet item 1

  - Bullet item 1-1

    - Bullet item 1-1-1

    - Bullet item 1-1-2

  - Bullet item 1-2

- Bullet item 2

  - Bullet item 2-1

  - Bullet item 2-2

## Numbered list `Support`

> 🎉 [Notion2Github](https://github.com/younho9/notion2github) support nested block.

1. Numbered item 1

   1. Numbered item 1-1

      1. Numbered item 1-1-1

      1. Numbered item 1-1-2

   1. Numbered item 1-2

1. Numbered item 2

   1. Numbered item 2-1

   1. Numbered item 2-2

## To-do list `Support`

> 🎉 [Notion2Github](https://github.com/younho9/notion2github) support nested block.

- [ ] To-do item 1

  - [ ] To-do item 1-1

    - [ ] To-do item 1-1-1

    - [ ] To-do item 1-1-2

  - [ ] To-do item 1-2

- [ ] To-do item 2

  - [ ] To-do item 2-1

  - [ ] To-do item 2-2

## Toggle list `Support`

> ⚠️ [Notion2Github](https://github.com/younho9/notion2github) doesn't support nested block.

<details><summary>Toggle item 1</summary>

<details><summary>Toggle item 1-1</summary>

<details><summary>Toggle item 1-1-1</summary>

<details><summary>Toggle item 1-1-2</summary>

</details>

<details><summary>Toggle item 1-2</summary>

</details>

</details>

<details><summary>Toggle item 2</summary>

<details><summary>Toggle item 2-1</summary>

<details><summary>Toggle item 2-2</summary>

</details>
