int main() {
  int x = 5;
  int y = 3;
  int z = 0;
  
  if (x > y) {
    z = x + y;
  } else {
    z = x * y;
  }

  for (int i = 0; i < 10; i = i + 1) {
    z = z + 1;
  }

  return z;
}
