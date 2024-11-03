console.log('fetching data...');
const todo1 = fetch('https://jsonplaceholder.typicode.com/todos/1').then(() =>
  console.log('fetching todo1 done!')
);
const todo2 = fetch('https://jsonplaceholder.typicode.com/todos/2').then(() =>
  console.log('fetching todo2 done!')
);
console.log('main thread done');
