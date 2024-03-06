from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from sklearn.preprocessing import LabelEncoder
import joblib
import matplotlib.pyplot as plt
import pandas as pd
import os 

TOKEN = '7019851646:AAETTCUSKAvPOgTDxobak3l9AyrS4uniCbM'
BOT_USERNAME: Final = '@PeaceGuardianBot'
df = pd.read_csv("violence_database_with_bias_v9_large_multi_entries.csv")

# Load the saved model along with the Label Encoders
model_filename = 'violence_prediction_model.joblib'
loaded_data = joblib.load(model_filename)

loaded_model = loaded_data['model']
le_country = loaded_data['le_country']
le_type_of_measures = loaded_data['le_type_of_measures']
le_form_of_violence = loaded_data['le_form_of_violence']


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # logic goes in here
    await update.message.reply_text('Hello there')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # logic goes in here
    await update.message.reply_text('Search important info')

async def get_recommendation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Extract the country name from the command
        country_name = context.args[0]

        # Encode the input country using the loaded Label Encoder
        encoded_country = le_country.transform([country_name])

        # Make prediction using the loaded model
        prediction = loaded_model.predict(encoded_country.reshape(-1, 1))

        # Decode the predicted label back to its original form
        predicted_form_of_violence = le_form_of_violence.inverse_transform(prediction)[0]
        predicted_type_of_measures = le_type_of_measures.inverse_transform(prediction)[0]

        # Reply with the predicted form of violence and type of measures
        await update.message.reply_text(f"The predicted form of violence in {country_name} is: {predicted_form_of_violence}")
        await update.message.reply_text(f"The predicted type of measures in {country_name} is: {predicted_type_of_measures}")

    except IndexError:
        await update.message.reply_text("Please provide a country name after the command.")
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {str(e)}")

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

async def show_chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Extract the country name from the command
        country_name = context.args[0]

        # Filter the DataFrame based on the selected country
        country_data = df[df['Country'] == country_name]

        # Calculate the percentage of each type of measure
        type_of_measure_percentage = country_data['Type of Measures'].value_counts(normalize=True) * 100

        # Calculate the percentage of each form of violence
        form_of_violence_percentage = country_data['Form of Violence'].value_counts(normalize=True) * 100

         # Plotting the charts
        plt.figure(figsize=(12, 8))

        plt.subplot(1, 2, 1)
        type_of_measure_percentage.plot(kind='bar', color='skyblue')
        plt.title('Percentage of Each Type of Measure')
        plt.xlabel('Type of Measure')
        plt.ylabel('Percentage')

        plt.subplot(1, 2, 2)
        form_of_violence_percentage.plot(kind='bar', color='lightcoral')
        plt.title('Percentage of Each Form of Violence')
        plt.xlabel('Form of Violence')
        plt.ylabel('Percentage')

        plt.tight_layout(pad=2.0)  # Increased padding

        # Save the chart as an image file
        chart_filename = f"{country_name}_charts.png"
        plt.savefig(chart_filename)

        # Send the charts to the user with 'await'
        with open(chart_filename, 'rb') as chart_file:
            await update.message.reply_photo(chart_file)

        # Remove the saved chart file
        os.remove(chart_filename)

    except IndexError:
        await update.message.reply_text("Please provide a country name after the command.")
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {str(e)}")

if __name__ == '__main__':
    print('Starting bot...')
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('get_recommendation', get_recommendation))
    app.add_handler(CommandHandler('show_chart', show_chart))


    # Errors
    app.add_error_handler(error)

    print('Polling...')
    app.run_polling(poll_interval=3)
