
<h4 class="attr-heading" id="create_dataset" data-toc-label="create_dataset" markdown>
  <tt><strong>create_dataset</strong>()</tt>
</h4>
<div markdown="block" class="indent">
A dataset defines the patients you want to include in your population and the
variables you want to extract for them.

A dataset definition file must define a dataset called `dataset`:

```py
dataset = create_dataset()
```

Add variables to the dataset as attributes:

```py
dataset.age = patients.age_on("2020-01-01")
```
</div>


<h4 class="attr-heading" id="Dataset" data-toc-label="Dataset" markdown>
  <tt><em>class</em> <strong>Dataset</strong>()</tt>
</h4>

<div markdown="block" class="indent">
Create a dataset with [`create_dataset`](#create_dataset).
<div class="attr-heading" id="Dataset.define_population">
  <tt><strong>define_population</strong>(<em>population_condition</em>)</tt>
  <a class="headerlink" href="#Dataset.define_population" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Define the condition that patients must meet to be included in the Dataset, in
the form of a [boolean patient series](#BoolPatientSeries) e.g.
```py
dataset.define_population(patients.date_of_birth < "1990-01-01")
```
</div>

<div class="attr-heading" id="Dataset.configure_dummy_data">
  <tt><strong>configure_dummy_data</strong>(<em>population_size</em>)</tt>
  <a class="headerlink" href="#Dataset.configure_dummy_data" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Configure the dummy data to be generated.

```py
dataset.configure_dummy_data(population_size=10000)
```
</div>

</div>
