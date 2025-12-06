from model import print_data, optimize_model, print_results

if __name__ == "__main__":
    print_data()

    model, x, y, z = optimize_model()

    print_results(model, x, y, z)
